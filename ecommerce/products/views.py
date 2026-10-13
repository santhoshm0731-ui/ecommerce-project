from rest_framework import status
from rest_framework.permissions import AllowAny,IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from products.models import( Category,SubCategory,
                             ProductImage,Product,ProductVariant)
from products.pagination import ProductPagination
from products.serializers import (CategorySerializer,SubcategorySerializer,
                                  ProductImageSerializer,ProductSerializer,ProductVariantSerializer)
from rest_framework.parsers import MultiPartParser, FormParser

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

class SubCategoryView(ModelViewSet):
    serializer_class = SubcategorySerializer

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        category_id = self.request.query_params.get('category')
        user = self.request.user
        if user and user.is_authenticated and user.is_staff:
            if category_id:
                return SubCategory.objects.filter(category=category_id)
            return SubCategory.objects.all()
        if category_id:
            return SubCategory.objects.filter(is_active=True, category=category_id)
        return SubCategory.objects.filter(is_active=True)


from rest_framework.filters import SearchFilter, OrderingFilter


class ProductView(ModelViewSet):
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    pagination_class = ProductPagination
    search_fields = ["name", "description"]
    ordering_fields = ["price", "name", "created_at"]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        subcategory_id = self.request.query_params.get("subcategory")
        user = self.request.user

        if user.is_authenticated and user.is_staff:
            if subcategory_id:
                return Product.objects.filter(
                    subcategory=subcategory_id
                )

            return Product.objects.all()

        if subcategory_id:
            return Product.objects.filter(
                is_active=True,
                subcategory=subcategory_id
            )

        return Product.objects.filter(
            is_active=True
        )


class ProductVariantView(ModelViewSet):
    serializer_class = ProductVariantSerializer

    def get_permissions(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return ProductVariant.objects.all()

        return ProductVariant.objects.filter(
            is_active=True,
            product__is_active=True
        )


class ProductImageView(ModelViewSet):
    serializer_class = ProductImageSerializer
    parser_classes = [MultiPartParser,FormParser]

    def get_permissions(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return ProductImage.objects.all()

        return ProductImage.objects.filter(
            product__is_active=True
        )





