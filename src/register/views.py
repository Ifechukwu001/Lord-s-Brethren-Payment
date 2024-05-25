from rest_framework import generics, status, serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer

from .serializers import RegisterSerializer


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    @extend_schema(
        responses={
            201: inline_serializer(
                name="RegisterTransactionLink",
                fields={
                    "status": serializers.CharField(),
                    "link": serializers.URLField(),
                },
            ),
            424: inline_serializer(
                name="RegisterTransactionFailed",
                fields={
                    "status": serializers.CharField(),
                    "message": serializers.CharField(),
                },
            ),
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        participant = serializer.save()
        link = participant.generate_payment_link()
        if not link:
            response_data = {"status": "failed", "message": "An error occurred"}
            return Response(response_data, status=status.HTTP_424_FAILED_DEPENDENCY)

        response_data = {"status": "success", "link": link}
        return Response(response_data, status=status.HTTP_201_CREATED)
