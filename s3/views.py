import boto3
from botocore.config import Config
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

class S3PresignedURLView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # The URL will look a bit like this:
        # https://backendurl.com/s3/upload-url?name=filename.png&type=image/png
        file_name = request.GET.get('name') # gets the filename from the URL
        file_type = request.GET.get('type') # gets the filetype from the URL

        # Invalidate the request if either of the required params are missing
        if not file_name:
            raise ValidationError({ 'detail': "Please provide a `name` parameter." })
        
        if not file_type:
            raise ValidationError({ 'detail': "Please provide a `type` parameter." })

        # Invoke the boto3 client to connect to s3 using the IAM credentials stored in our settings.py file.
        # This is like connection to mongodb using mongoose.connect()
        s3 = boto3.client(
            's3',
            region_name=settings.AWS_S3_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
            config=Config(signature_version='s3v4')
        )

        # Once authenticated, the `s3` module has a method for obtaining pre-signed URLs
        # The specified `ClientMethod` MUST be an allowed action
        # We created a permission that explicity allowed PutObject actions on our bucket
        # This URL will be valid to PUT objects to our s3 bucket, for 60 seconds only
        presigned_url = s3.generate_presigned_url(
            ClientMethod='put_object', # PutObject Allowed thanks to our custom permission
            Params={
                'Bucket': settings.AWS_S3_BUCKET, # Which bucket to store in?
                'Key': file_name, # Under which name?
                'ContentType': file_type # Which file type?
            },
            ExpiresIn=60 # How long this URL will be valid for once it's been generated.
        )

        # Once uploaded, this is where the file will be accessible.
        # We're using the CloudFront domain we setup as a CDN here.
        final_image_url = f"https://{settings.AWS_CLOUDFRONT_DOMAIN}/{file_name}"

        return Response({
            'presigned_url': presigned_url, # The URL we'll use to upload an image
            'final_image_url': final_image_url # The URL the image will live on once uploaded - this is what will be saved to the database
        })