from rest_framework import status
from rest_framework.permissions import AllowAny,IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from products.models import( Category,SubCategory,
                             ProductImage,Product,ProductVariant)
from products.serializers import (CategorySerializer,SubcategorySerializer,
                                  ProductImageSerializer,ProductSerializer,ProductVariantSerializer)

class CategoryView(APIView):
    def get_permissions(self):
        if self.request.method== 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self,request,category_id=None):
        if category_id is not None:
            try:
                category=Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return Response(
                    {
                        'error':'Category not found.'

                    },
                    status=status.HTTP_404_NOT_FOUND
               )
            data=CategorySerializer(category)
            return Response(
                {
                    'message':'Here is the Category',
                    'category':data.data
                },
                status=status.HTTP_200_OK
            )
        categories=CategorySerializer(Category.objects.all(),many=True)
        return Response(
            {
                'message':'All Categories',
                'categories':categories.data
            },
            status=status.HTTP_200_OK
        )

    def post(self,request):
        data=request.data
        serializer=CategorySerializer(data=data)
        serializer.is_valid(
            raise_exception=True
        )
        category=serializer.save()
        return Response(
            {
                'message':'Category created successfully.',
                'id':category.id
            },
            status=status.HTTP_201_CREATED
        )

    def patch(self,request,category_id):

        try:
            category=Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response(
                {
                    'error':'Category not exist',

                },
                status=status.HTTP_404_NOT_FOUND
            )
        update_data=request.data
        serializer = CategorySerializer(instance=category,data=update_data,partial=True)
        if not serializer.is_valid():
            return Response(
                {
                    'message':'unable to update category',
                    'error':serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(
            {
                'message':'Category updated successfully.',
                'id':category_id,
                'data':serializer.data
            },
            status=status.HTTP_200_OK
        )

    def delete(self,request,category_id):

        try:
            category=Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response(
                {
                    'error':'Category not exist'
                },status=status.HTTP_404_NOT_FOUND
            )
        category.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


