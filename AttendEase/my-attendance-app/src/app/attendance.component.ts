import { Component, OnInit } from '@angular/core';
import { AttendanceService } from '../services/attendance.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-attendance',
  standalone: true,
  imports: [CommonModule, FormsModule],
  providers: [DatePipe],
  templateUrl: './attendance.component.html',
  styleUrls: ['./attendance.component.css'],
})
export class AttendanceComponent implements OnInit {
  attendanceRecords: any[] = [];
  selectedClassId: string = ''; 

  constructor(private attendanceService: AttendanceService) {}

  ngOnInit(): void {
    this.loadAttendance();
  }

  /** ✅ Load attendance records */
  loadAttendance(): void {
    this.attendanceService.getAttendance().subscribe({
      next: (records: any) => {
        this.attendanceRecords = records.map((record: any) => ({
          ...record,
          module: record.module || "Unknown Module",  // ✅ Ensure module is displayed
          session_type: record.session_type || "Unknown Type"  // ✅ Ensure session type is displayed
        }));        
      },
      error: (error: any) => {
        console.error("Error fetching attendance:", error);
      }
    });
  }  

  /** ✅ Mark attendance for a specific class */
  markAttendance(): void {  
    if (!this.selectedClassId) {  
      console.warn('⚠️ No class selected for attendance');
      return;
    }

    this.attendanceService.markAttendance(this.selectedClassId).subscribe({
      next: (response: any) => {
        console.log('✅ Attendance marked:', response);
        this.loadAttendance(); 
      },
      error: (error: any) => {
        console.error('❌ Error marking attendance:', error);
      },
    });
  }

  openCameraPopup(): void {
    const width = 1000;  // ✅ Set width
    const height = 830; // ✅ Set height
    const left = (window.screen.width - width) / 2;
    const top = (window.screen.height - height) / 2;

    const popup = window.open(
      'http://localhost:5000/camera-popup', 
      'CameraPopup',
      `width=${width},height=${height},left=${left},top=${top},resizable=no,scrollbars=no`
    );

    if (!popup) {
      alert('⚠️ Pop-up blocked! Enable pop-ups for this site.');
    }
  }
}
