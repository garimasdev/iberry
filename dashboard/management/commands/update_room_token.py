from django.core.management.base import BaseCommand
from dashboard.models import Room
from accounts.models import User
import hashlib

class Command(BaseCommand):
    help = 'Update room tokens for user Willow'

    def handle(self, *args, **kwargs):
        # Find the user "Willow"
        willow_user = User.objects.filter(username='willow').first()
        print(willow_user)

        if not willow_user:
            self.stdout.write(self.style.ERROR("User 'Willow' not found."))
            return

        # Get all rooms for the user
        rooms = Room.objects.filter(user=willow_user)

        if not rooms.exists():
            self.stdout.write(self.style.WARNING("No rooms found for user 'Willow'."))
            return

        # Update room tokens
        for room in rooms:
            room.room_token = hashlib.md5(f"{willow_user.username}_{room.room_number}".encode()).hexdigest()
            room.save()
            print("room updated")
            self.stdout.write(self.style.SUCCESS(f"Updated room_token for room {room.room_number}."))

        self.stdout.write(self.style.SUCCESS("Successfully updated room tokens for user 'Willow'."))
