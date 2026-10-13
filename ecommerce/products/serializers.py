from itertools import product

from rest_framework import serializers

from products.models import (
    Category,
    SubCategory,
    Product,
    ProductVariant,
    ProductImage,
)


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True,
        max_length=100
    )

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Please enter a valid name."
            )

        return value

    def validate_description(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Please enter description."
            )

        return value

    def create(self, validated_data):
        return Category.objects.create(**validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class SubcategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True,
        max_length=100
    )

    class Meta:
        model = SubCategory
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
            "category",
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Please enter a valid name."
            )

        return value

    def validate_description(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Please enter description."
            )

        return value

    def create(self, validated_data):
        return SubCategory.objects.create(**validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class ProductVariantSerializer(serializers.ModelSerializer):
    size = serializers.CharField(
        required=True,
        max_length=20
    )

    color = serializers.CharField(
        required=True,
        max_length=20
    )

    price = serializers.DecimalField(
        required=True,
        max_digits=10,
        decimal_places=2
    )

    stock = serializers.IntegerField(
        required=True,
        min_value=0
    )

    sku = serializers.CharField(
        required=True
    )

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "size",
            "color",
            "price",
            "stock",
            "sku",
            "is_active",
            "created_at",
            "updated_at",
            "product",
        ]

    def validate_size(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Size is required."
            )

        return value

    def validate_color(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Color is required."
            )

        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than 0."
            )

        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Stock cannot be negative."
            )

        return value

    def create(self, validated_data):
        return ProductVariant.objects.create(**validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class ProductImageSerializer(serializers.ModelSerializer):
    alt_text = serializers.CharField(
        required=True,
        max_length=100
    )

    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image",
            "alt_text",
            "is_primary",
            "created_at",
            "product",
        ]

    def validate_alt_text(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Alt text is required."
            )

        return value

    def create(self, validated_data):
        product = validated_data.get("product")

        if validated_data.get("is_primary", False):
            ProductImage.objects.filter(
                product=product,
                is_primary=True
            ).update(is_primary=False)

        return ProductImage.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if validated_data.get("is_primary", False):
            ProductImage.objects.filter(
                product=instance.product,
                is_primary=True
            ).exclude(
                id=instance.id
            ).update(is_primary=False)

        return super().update(instance, validated_data)


class ProductSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True,
        max_length=100
    )
    variants=ProductVariantSerializer(many=True,read_only=True)
    images=ProductImageSerializer(many=True,read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
            "subcategory",
            "variants",
            "images"
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Please enter a valid name."
            )

        return value

    def validate_description(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Please enter description."
            )
        return value

    def create(self, validated_data):
        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)



