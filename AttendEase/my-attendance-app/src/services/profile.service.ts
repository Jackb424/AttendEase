import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError, of } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class ProfileService {
  private apiUrl = 'http://localhost:5000/api/v1.0';

  constructor(private http: HttpClient, @Inject(PLATFORM_ID) private platformId: any) {}

  getProfile(): Observable<any> {
    if (!isPlatformBrowser(this.platformId)) {
      console.warn('Not running in a browser environment, skipping profile request.');
      return of(null); // ✅ Prevents errors when running in non-browser environments
    }

    const token = localStorage.getItem('x-access-token');
    
    if (!token) {
      console.warn('Token is missing, redirecting to login...');
      return of(null); // ✅ Avoids throwing an error, just returns `null`
    }

    const headers = new HttpHeaders({ 'x-access-token': token });

    return this.http.get(`${this.apiUrl}/profile`, { headers }).pipe(
      catchError((error) => {
        console.error('Failed to load profile:', error);
        return throwError(() => new Error(error));
      })
    );
  }

  updateProfile(formData: FormData): Observable<any> { 
    let token = '';

    if (isPlatformBrowser(this.platformId)) {
      token = localStorage.getItem('x-access-token') ?? '';
    }

    return this.http.put(`${this.apiUrl}/profile`, formData, {
      headers: new HttpHeaders({ 'x-access-token': token })
    });
  }
}
