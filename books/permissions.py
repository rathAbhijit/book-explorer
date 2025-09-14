from rest_framework import permissions

# Only the owner can edit/delete their review or interaction
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission: Object-level permission to only allow owners of an object to edit it.
    Read-only requests are allowed for everyone.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        return obj.user == request.user
