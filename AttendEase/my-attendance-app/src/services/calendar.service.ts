import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class CalendarService {
  private apiUrl = 'http://localhost:5000/api/v1.0/calendar';

  constructor(
    private http: HttpClient,
    @Inject(PLATFORM_ID) private platformId: Object // ✅ Detects if it's running in a browser
  ) {}

  getUserSchedule(): Observable<any> {
    if (!isPlatformBrowser(this.platformId)) {
      console.warn('Not running in a browser environment, skipping request.');
      return of(null); // ✅ Prevents errors in SSR
    }

    const token = localStorage.getItem('x-access-token');
    if (!token) {
      console.warn('Token is missing, skipping request.');
      return of(null); // ✅ Prevents errors if token is missing
    }

    const headers = new HttpHeaders({ 'x-access-token': token });

    return this.http.get(this.apiUrl, { headers }).pipe(
      catchError((error) => {
        console.error('Failed to load calendar data:', error);
        return of([]);
      })
    );
  }
}
