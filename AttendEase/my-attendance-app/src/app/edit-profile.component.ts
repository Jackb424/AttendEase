import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { ProfileService } from '../services/profile.service';
import { Router } from '@angular/router';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-edit-profile',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './edit-profile.component.html',
  styleUrls: ['./edit-profile.component.css']
})
export class EditProfileComponent implements OnInit {
  user: any = { course: '', campus_location: '', profile_image: '' };
  selectedFile: File | null = null;
  isAdmin: boolean = false;  // ✅ Track admin status

  courses = ['Computer Science', 'Software Engineering', 'Cyber Security', 'Data Science', 'AI & Machine Learning'];
  campusLocations = ['Belfast', 'Derry/ Londonderry', 'Coleraine'];

  constructor(
    private profileService: ProfileService,
    private router: Router,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    this.loadProfile();
  }

  loadProfile(): void {
    this.profileService.getProfile().subscribe(
      (data) => {
        if (data) {
          this.user = data;
          this.isAdmin = data.is_admin || false;  // ✅ Check if user is admin
        } else {
          console.warn('No profile data found, redirecting to login...');
          this.router.navigate(['/login']);
        }
      },
      (error) => {
        console.error('Failed to load profile:', error);
        this.router.navigate(['/login']);
      }
    );
  }

  onFileSelected(event: any): void {
    const file: File = event.target.files[0];
  
    if (file) {
      const allowedTypes = ['image/jpeg', 'image/png'];
  
      if (!allowedTypes.includes(file.type)) {
        alert('⚠️ Invalid file type. Please upload a JPG or PNG image.');
        this.selectedFile = null;
        (event.target as HTMLInputElement).value = '';  // Reset file input
        return;
      }
  
      this.selectedFile = file;
    }
  }
  

  saveProfile(): void {
    const formData = new FormData();
    formData.append('course', this.user.course);
    formData.append('campus_location', this.user.campus_location);
  
    if (this.selectedFile) {
      formData.append('face_image', this.selectedFile);
    }
  
    this.profileService.updateProfile(formData).subscribe(
      (response: any) => {
        console.log('Profile updated successfully');
        if (response.profile_image) {
          this.user.profile_image = response.profile_image + '?t=' + new Date().getTime();  // ✅ Force image refresh
        }
        this.router.navigate(['/profile']);
      },
      (error) => {
        console.error('Error updating profile:', error);
      }
    );
  }  
}
