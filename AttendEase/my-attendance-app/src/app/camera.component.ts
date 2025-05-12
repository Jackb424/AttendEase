import { Component, OnInit } from '@angular/core';
import { CameraService } from '../services/camera.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-camera',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './camera.component.html',
  styleUrls: ['./camera.component.css'],
})
export class CameraComponent implements OnInit {
  timetable: any[] = [];
  ongoingClass: any = null;
  tracking: boolean = false;

  constructor(private cameraService: CameraService) {}

  ngOnInit(): void {
    this.cameraService.getTimetable().subscribe({
      next: (data) => {
        this.timetable = data;
        this.checkOngoingClass();
      },
      error: (err) => console.error('Error fetching timetable:', err),
    });
  }

  checkOngoingClass(): void {
    const now = new Date();
    this.ongoingClass = this.timetable.find((cls) => {
      const start = new Date(cls.start_time);
      const end = new Date(cls.end_time);
      return now >= start && now <= end;
    });
  }

  startTracking(): void {
    if (!this.ongoingClass) {
      alert('❌ No active class found.');
      return;
    }

    this.tracking = true;

    this.cameraService.startTracking().subscribe({
      next: (response) => console.log('✅ Attendance marked:', response),
      error: (err) => console.error('❌ Error marking attendance:', err),
    });
  }
}
