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


