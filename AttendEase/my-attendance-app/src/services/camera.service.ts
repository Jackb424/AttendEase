import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class CameraService {
  private apiUrl = 'http://localhost:5000/api/v1.0';

  constructor(private http: HttpClient) {}

  /** ✅ Fetch timetable from MongoDB */
  getTimetable(): Observable<any> {
    return this.http.get(`${this.apiUrl}/timetable`);  // ✅ Corrected API Route
  }

  /** ✅ Start facial recognition tracking */
  startTracking(): Observable<any> {
    return this.http.post(`${this.apiUrl}/attendance/mark-attendance`, {});
  }
}
