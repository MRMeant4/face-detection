import os
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import magic
import uuid
from pathlib import Path
from django.http import JsonResponse, HttpRequest
from .detector import FaceDetector


@csrf_exempt
def upload_image(request: HttpRequest) -> JsonResponse:
    """
    Handle the image upload request.

    Args:
        request: Django HTTP request object

    Returns:
        JsonResponse: JSON response object
    """
    is_valid, error_response, validated_data = validate_request(request)
    if not is_valid:
        return error_response

    filename = validated_data["filename"]
    upload_path = Path("uploaded") / filename

    file_path = default_storage.save(
        str(upload_path), ContentFile(validated_data["file_content"])
    )
    file_full_path = os.path.join(settings.MEDIA_ROOT, file_path)

    try:
        detector = FaceDetector()
        processed_path, faces_count = detector.process_image(
            Path(file_full_path), validated_data["unique_id"]
        )

        image_url = f"{request.scheme}://{request.get_host()}/media/{processed_path}"

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "faces",
            {
                "type": "face_detection_notification",
                "image_url": image_url,
                "faces_detected": faces_count,
            },
        )

        return JsonResponse(
            {"success": True, "image_url": image_url, "faces_detected": faces_count},
            status=200,
        )

    except FileNotFoundError as e:
        return JsonResponse({"error": "File not found: " + str(e)}, status=404)
    except ValueError as e:
        return JsonResponse({"error": "Value error: " + str(e)}, status=400)
    except Exception as e:
        return JsonResponse(
            {"error": "An unexpected error occurred: " + str(e)}, status=500
        )


def validate_request(
    request: HttpRequest,
) -> tuple[bool, JsonResponse | None, dict | None]:
    """
    Validate the image upload request.

    Args:
        request: Django HTTP request object

    Returns:
        tuple: (is_valid, error_response, validated_data)
            - is_valid: Boolean indicating if the request is valid
            - error_response: JsonResponse object if validation fails, None otherwise
            - validated_data: Dictionary containing validated data if successful, None otherwise
    """
    if request.method != "POST":
        return (
            False,
            JsonResponse({"error": "Only POST requests are allowed"}, status=405),
            None,
        )

    if "image" not in request.FILES:
        return (
            False,
            JsonResponse({"error": "No image file provided"}, status=400),
            None,
        )

    image_file = request.FILES["image"]
    file_content = image_file.read()
    mime = magic.Magic(mime=True)
    content_type = mime.from_buffer(file_content)

    if not content_type.startswith("image/"):
        return (
            False,
            JsonResponse(
                {
                    "error": f"Uploaded file is not an image. Detected type: {content_type}"
                },
                status=400,
            ),
            None,
        )

    unique_id = str(uuid.uuid4())
    file_extension = os.path.splitext(image_file.name)[1]
    filename = f"upload_{unique_id}{file_extension}"

    return (
        True,
        None,
        {
            "file_content": file_content,
            "filename": filename,
            "unique_id": unique_id,
        },
    )
