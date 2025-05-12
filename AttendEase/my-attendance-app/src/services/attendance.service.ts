import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { isPlatformBrowser } from '@angular/common'; // ✅ Import check for browser

@Injectable({
  providedIn: 'root',
})
export class AttendanceService {
  private apiUrl = 'http://localhost:5000/api/v1.0/attendance';

  constructor(private http: HttpClient, @Inject(PLATFORM_ID) private platformId: object) {}

  /** ✅ Get token safely */
  private getToken(): string {
    if (isPlatformBrowser(this.platformId)) { // ✅ Ensure we are in the browser
      return localStorage.getItem('x-access-token') || '';
    }
    return ''; // Return empty string if not in browser
  }

  /** ✅ Fetch attendance records */
  getAttendance(): Observable<any> {
    const token = this.getToken();
    return this.http.get(`${this.apiUrl}`, {
      headers: new HttpHeaders({ 'x-access-token': token }),
    });
  }

  getAllAttendance(): Observable<any> {
    const token = this.getToken();
    return this.http.get(`${this.apiUrl}/all`, {
      headers: new HttpHeaders({ 'x-access-token': token }),
    });
  }  

  /** ✅ Mark attendance for a specific class */
  markAttendance(classId: string): Observable<any> {
    const token = this.getToken();
    return this.http.post(
      `${this.apiUrl}/mark-attendance`,
        { classId }, // ✅ Pass class ID to backend
        { headers: new HttpHeaders({ 'x-access-token': token }) }
      );
    }

  /** ✅ Fetch audit logs */
  getAuditLogs(): Observable<any> {
    const token = this.getToken();
    return this.http.get(`${this.apiUrl}/audit-logs`, {
      headers: new HttpHeaders({ 'x-access-token': token }),
    });
  }

  /** ✅ Update attendance */
  updateAttendance(record: any): Observable<any> {
    const token = this.getToken();
    return this.http.put(`${this.apiUrl}/update`, record, {
      headers: new HttpHeaders({ 'x-access-token': token }),
    });
  }

  /** ✅ Delete attendance */
  deleteAttendance(recordId: string): Observable<any> {
    const token = this.getToken();
    return this.http.delete(`${this.apiUrl}/delete/${recordId}`, {
      headers: new HttpHeaders({ 'x-access-token': token }),
    });
  }
  
  /** ✅ Get analytics data */
  getAnalytics(): Observable<any> {
    const token = this.getToken();
    return this.http.get(`${this.apiUrl}/analytics`, {
      headers: new HttpHeaders({ 'x-access-token': token }),
    });
  }

  getAbsentees(): Observable<any> {
    const token = this.getToken();
    return this.http.get(`${this.apiUrl}/absentees`, {
      headers: new HttpHeaders({ 'x-access-token': token }),
    });
  }

  deleteAbsentee(absenteeId: string): Observable<any> {
    return this.http.delete(`http://localhost:5000/api/v1.0/absentees/delete/${absenteeId}`, {
      headers: new HttpHeaders({ 'x-access-token': this.getToken() })
    });
  }  
}
