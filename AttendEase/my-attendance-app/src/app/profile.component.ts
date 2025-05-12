import { Component, OnInit } from '@angular/core';
import { ProfileService } from '../services/profile.service';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule], 
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css']
})
export class ProfileComponent implements OnInit {
  user: any = {};
  isAdmin: boolean = false;  // ✅ Track admin status

  constructor(private profileService: ProfileService, private router: Router) {}

  ngOnInit(): void {
    this.loadProfile();
  }

  loadProfile(): void {
    this.profileService.getProfile().subscribe(
      (data) => {
        if (!data) {
          console.warn('No profile data found, redirecting to login...');
          this.router.navigate(['/login']);
        } else {
          this.user = data;
          this.isAdmin = data.is_admin || false;  // ✅ Check if user is admin
        }
      },
      (error) => {
        console.error('Failed to load profile:', error);
        this.router.navigate(['/login']);
      }
    );
  }

  /**
   * ✅ Appends a timestamp to force image refresh
   */
  getProfileImage(): string {
    return this.user.profile_image ? `${this.user.profile_image}?t=${Date.now()}` : 'assets/default-profile.jpg';
  }

  navigateToEditProfile(): void {
    this.router.navigate(['/edit-profile']);
  }
}