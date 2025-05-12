import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { Router } from '@angular/router';
import { isPlatformBrowser } from '@angular/common';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private apiUrl = 'http://localhost:5000/api/v1.0';

  constructor(
    private http: HttpClient, 
    private router: Router,
    @Inject(PLATFORM_ID) private platformId: Object 
  ) {}

  signup(userData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/signup`, userData);
  }

  login(b0_number: string, password: string): Observable<{ 'x-access-token': string, user: { name: string } }> { 
    return this.http.post<{ 'x-access-token': string, user: { name: string } }>(`${this.apiUrl}/login`, { b0_number, password }).pipe(
        tap(response => {
            console.log("📩 Server Response:", response); // ✅ Debugging Log

            if (response && response['x-access-token']) {
                localStorage.setItem('x-access-token', response['x-access-token']); // ✅ Save token
                localStorage.setItem('user-name', response.user.name); // ✅ Save correct user name
                console.log("✅ Saved User Name:", response.user.name); // ✅ Debugging Log
                this.router.navigate(['/profile']); // ✅ Redirect to profile page
            }
        })
    );
  }

  logout(): Observable<any> {
    if (!isPlatformBrowser(this.platformId)) return new Observable();

    const token = localStorage.getItem('x-access-token') ?? '';
    localStorage.removeItem('x-access-token');
    window.dispatchEvent(new Event('logoutSuccess'));

    return this.http.get(`${this.apiUrl}/logout`, {
      headers: new HttpHeaders({ 'x-access-token': token })
    }).pipe(
      tap(() => this.router.navigate(['/login']))
    );
  }

  isTokenExpired(): boolean {
    const token = localStorage.getItem('x-access-token');
    if (!token) return true;
  
    try {
      const decoded = JSON.parse(atob(token.split('.')[1])); // Decode JWT
      const exp = decoded.exp * 1000; // Convert to milliseconds
      return Date.now() > exp; // Check if expired
    } catch (e) {
      console.error('Error decoding token:', e);
      return true; // Treat as expired if decoding fails
    }
  }
  
}
