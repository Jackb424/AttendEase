import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AttendanceService } from '../services/attendance.service';

@Component({
  selector: 'admin-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.css'],
  providers: [AttendanceService]
})
export class AdminComponent implements OnInit {
  attendanceRecords: any[] = [];  // Stores original records
  filteredRecords: any[] = [];  // Stores filtered records for live search
  paginatedRecords: any[] = [];
  auditLogs: any[] = [];
  paginatedLogs: any[] = [];
  absentees: any[] = [];
  paginatedAbsentees: any[] = [];

  filterB0: string = '';  // Filter for B0 Number
  filterClass: string = '';  // Filter for Class Name
  filterDate: string = '';  // Filter for Date

  selectedRecord: any = null;

  currentPageRecords: number = 1;
  totalPagesRecords: number = 1;
  currentPageLogs: number = 1;
  totalPagesLogs: number = 1;
  currentPageAbsentees: number = 1;
  totalPagesAbsentees: number = 1;
  recordsPerPage: number = 8;

  constructor(private attendanceService: AttendanceService) {}

  ngOnInit(): void {
    this.fetchAttendanceRecords();
    this.fetchAuditLogs();
    this.fetchAbsentees(); 
  }

  fetchAttendanceRecords(): void {
    this.attendanceService.getAllAttendance().subscribe(
      (records: { attendance_time: string }[]) => { 
        this.attendanceRecords = (records || []).sort((a, b) => 
          new Date(b.attendance_time).getTime() - new Date(a.attendance_time).getTime()
        ); // 🔥 Sorts records from latest to oldest
        this.updateFilters();
      },
      (error: any) => {
        console.error('Error fetching attendance:', error);
      }
    );
  }
  

  fetchAuditLogs(): void {
    this.attendanceService.getAuditLogs().subscribe(
      (logs: { timestamp: string }[]) => { // ✅ Explicitly define timestamp as string
        this.auditLogs = (logs || []).sort((a, b) => 
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        ); // 🔥 Sort logs from latest to oldest
        this.totalPagesLogs = Math.ceil(this.auditLogs.length / this.recordsPerPage); // ✅ Ensure total pages is calculated
        this.currentPageLogs = 1; // ✅ Reset to first page
        this.paginateLogs();
      },
      (error: any) => {
        console.error('Error fetching audit logs:', error);
      }
    );
  }


  updateFilters(): void {
    this.filteredRecords = this.attendanceRecords.filter(record => {
      const b0 = record.b0_number ? record.b0_number.toLowerCase() : '';
      const mod = record.module ? record.module.toLowerCase() : '';
      const date = record.attendance_time ? record.attendance_time : '';

      return (!this.filterB0 || b0.includes(this.filterB0.toLowerCase())) &&
             (!this.filterClass || mod.includes(this.filterClass.toLowerCase())) &&
             (!this.filterDate || date.startsWith(this.filterDate));
    });

    this.totalPagesRecords = Math.ceil(this.filteredRecords.length / this.recordsPerPage);
    this.currentPageRecords = 1;
    this.paginateRecords();
  }

  paginateRecords(): void {
    const startIndex = (this.currentPageRecords - 1) * this.recordsPerPage;
    this.paginatedRecords = this.filteredRecords.slice(startIndex, startIndex + this.recordsPerPage);
  }

  paginateLogs(): void {
    const startIndex = (this.currentPageLogs - 1) * this.recordsPerPage;
    this.paginatedLogs = this.auditLogs.slice(startIndex, startIndex + this.recordsPerPage);
  }

  nextPageRecords(): void {
    if (this.currentPageRecords < this.totalPagesRecords) {
      this.currentPageRecords++;
      this.paginateRecords();
    }
  }

  prevPageRecords(): void {
    if (this.currentPageRecords > 1) {
      this.currentPageRecords--;
      this.paginateRecords();
    }
  }

  nextPageLogs(): void {
    if (this.currentPageLogs < this.totalPagesLogs) {
      this.currentPageLogs++;
      this.paginateLogs();
    }
  }

  prevPageLogs(): void {
    if (this.currentPageLogs > 1) {
      this.currentPageLogs--;
      this.paginateLogs();
    }
  }

  paginateAbsentees(): void {
    const startIndex = (this.currentPageAbsentees - 1) * this.recordsPerPage;
    this.paginatedAbsentees = this.absentees.slice(startIndex, startIndex + this.recordsPerPage);
  }

  nextPageAbsentees(): void {
    if (this.currentPageAbsentees < this.totalPagesAbsentees) {
      this.currentPageAbsentees++;
      this.paginateAbsentees();
    }
  }
  
  prevPageAbsentees(): void {
    if (this.currentPageAbsentees > 1) {
      this.currentPageAbsentees--;
      this.paginateAbsentees();
    }
  }

  /** ✅ Select a record to edit */
  editAttendance(record: any): void {
    this.selectedRecord = { ...record };
  }

  /** ✅ Save updated attendance */
  saveAttendance(): void {
    if (!this.selectedRecord) return;

    this.attendanceService.updateAttendance(this.selectedRecord).subscribe(
      () => {
        alert("✅ Attendance updated successfully!");
        this.fetchAttendanceRecords();
        this.fetchAuditLogs();
        this.selectedRecord = null;
      },
      (error: any) => { 
        console.error("❌ Error updating attendance:", error); 
      }
    );
  }

  deleteAttendance(recordId: string): void {
    if (confirm("Are you sure you want to delete this record?")) {
      this.attendanceService.deleteAttendance(recordId).subscribe(
        () => {
          alert("✅ Attendance deleted!");
          this.fetchAttendanceRecords();
          this.fetchAuditLogs();
        },
        (error: any) => { 
          console.error("❌ Error deleting attendance:", error); 
        }
      );
    }
  }

  fetchAbsentees(): void {
    this.attendanceService.getAbsentees().subscribe(
      (data) => {
        this.absentees = data;
        this.totalPagesAbsentees = Math.ceil(this.absentees.length / this.recordsPerPage);
        this.currentPageAbsentees = 1;
        this.paginateAbsentees();
      },
      (error) => {
        console.error("❌ Error fetching absentees:", error);
      }
    );
  }

  deleteAbsentee(absentee: any): void {
    if (confirm(`Are you sure you want to delete absentee record for ${absentee.name}?`)) {
      this.attendanceService.deleteAbsentee(absentee._id).subscribe(
        () => {
          alert("✅ Absentee removed & added to attendance.");
          this.fetchAbsentees();
          this.fetchAttendanceRecords();
          this.fetchAuditLogs();
        },
        (error) => {
          console.error("❌ Error deleting absentee:", error);
        }
      );
    }
  }
  

  /** ✅ Open camera pop-up for attendance marking */
  openCameraPopup(): void {
    const width = 1000;  
    const height = 830;  
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
