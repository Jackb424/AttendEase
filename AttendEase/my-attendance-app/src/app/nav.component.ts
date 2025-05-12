import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'navigation',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './nav.component.html',
  styleUrls: ['./nav.component.css']
})
export class NavComponent implements OnInit {
  isAuthenticated: boolean = false;
  isAdmin: boolean = false;
  userName: string | null = null; // ✅ Store user's name

  constructor(
    private router: Router, 
    private authService: AuthService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    this.updateAuthStatus();
    if (isPlatformBrowser(this.platformId)) { 
      window.addEventListener('loginSuccess', () => this.updateAuthStatus());
      window.addEventListener('logoutSuccess', () => this.updateAuthStatus());
    }
  }

  updateAuthStatus(): void {
    if (isPlatformBrowser(this.platformId)) { 
      const token = localStorage.getItem('x-access-token');
      this.isAuthenticated = !!token;
      
      const storedUserName = localStorage.getItem('user-name');
      console.log("🔍 Stored User Name:", storedUserName); // ✅ Debugging Log
      this.userName = storedUserName ? storedUserName : 'Profile'; // ✅ Fallback to 'Profile' if null

      this.isAdmin = token ? this.decodeToken(token)?.admin || false : false;
    }
}


  logout(): void {
    this.authService.logout().subscribe({
      next: () => {
        localStorage.removeItem('user-name'); // ✅ Clear name on logout
        window.dispatchEvent(new Event('logoutSuccess'));
        this.router.navigate(['/login']); 
      },
      error: (error: any) => {
        console.error('Logout failed:', error);
      }
    });
  }

  private decodeToken(token: string): any {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => `%${c.charCodeAt(0).toString(16).padStart(2, '0')}`)
          .join('')
      );
      return JSON.parse(jsonPayload);
    } catch (e) {
      console.error('Token decode error', e);
      return null;
    }
  }
}
