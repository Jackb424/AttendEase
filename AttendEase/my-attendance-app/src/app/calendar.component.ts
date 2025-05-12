import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { CalendarOptions } from '@fullcalendar/core';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import { FullCalendarModule } from '@fullcalendar/angular';
import { CalendarService } from '../services/calendar.service';
import { CommonModule, isPlatformBrowser } from '@angular/common';

@Component({
  selector: 'app-calendar',
  standalone: true,
  imports: [CommonModule, FullCalendarModule], // ✅ Ensure FullCalendarModule is imported
  templateUrl: './calendar.component.html',
  styleUrls: ['./calendar.component.css']
})
export class CalendarComponent implements OnInit {
  calendarOptions: CalendarOptions = {
    initialView: 'timeGridWeek',
    plugins: [dayGridPlugin, timeGridPlugin],
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay'
    },
    firstDay: 1, // Monday as first day
    slotMinTime: "09:00:00", // Start at 9 AM
    slotMaxTime: "19:00:00", // End at 7 PM
    slotLabelInterval: "01:00:00", // ✅ Show labels every 1 hour instead of 30 minutes
    slotDuration: "01:00:00", // ✅ Make grid lines appear every 1 hour
    allDaySlot: false,
    weekends: false,
    events: [],
    nowIndicator: true, // ✅ Show a red line for the current time
  
    // ✅ Handle clicking on a session
    eventClick: (info) => {
      alert(`📚 Class Info:
      - Module: ${info.event.title}
      - Start: ${info.event.start?.toLocaleString()}
      - End: ${info.event.end?.toLocaleString()}
      - Type: ${info.event.extendedProps['sessionType']}
      - Room: ${info.event.extendedProps['room'] || 'TBA'}
      - Lecturer: ${info.event.extendedProps['lecturer'] || 'TBA'}`);
    },
    
    eventMouseEnter: (info) => {
      const calendarContainer = document.querySelector('.calendar-container');
      if (!calendarContainer) return;
    
      const tooltip = document.createElement('div');
      tooltip.className = 'tooltip-class visible';
      tooltip.style.top = `${info.jsEvent.clientY + 10}px`;
      tooltip.style.left = `${info.jsEvent.clientX + 10}px`;
    
      tooltip.innerHTML = `
        <strong>${info.event.title}</strong><br>
        <span class="time">🕒 ${info.event.start?.toLocaleTimeString()} - ${info.event.end?.toLocaleTimeString()}</span><br>
        <span class="room">📍 Room: ${info.event.extendedProps['room'] || 'TBA'}</span><br>
        <span class="lecturer">👨‍🏫 Lecturer: ${info.event.extendedProps['lecturer'] || 'TBA'}</span>
      `;
    
      calendarContainer.appendChild(tooltip);
      tooltip.style.position = 'absolute';
      tooltip.style.zIndex = '9999';
    
      info.el.addEventListener('mouseleave', () => {
        tooltip.classList.remove('visible');
        setTimeout(() => tooltip.remove(), 200);
      });
    }    
  }    

  isBrowser: boolean; // ✅ Check if running in browser
  loading = true; // ✅ Add loading state
  errorMessage = ''; // ✅ Add error state

  constructor(
    private calendarService: CalendarService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    this.isBrowser = isPlatformBrowser(this.platformId); // ✅ Detects if running in browser
  }

  ngOnInit(): void {
    if (this.isBrowser) { // ✅ Ensure it only runs in the browser
      this.loadSchedule();
    } else {
      console.warn('FullCalendar is disabled in non-browser environments.');
    }
  }

  loadSchedule(): void {
    this.calendarService.getUserSchedule().subscribe(
      (data) => {
        console.log("📅 Fetched Schedule Data:", data); // ✅ Check if data is coming
        this.loading = false;
        
        if (!data || data.length === 0) {
          console.warn("⚠️ No schedule data available.");
          this.errorMessage = '⚠️ No scheduled classes found.';
          return;
        }
  
        // Flatten occurrences into an array
        this.calendarOptions.events = data.flatMap((session: any) =>
          this.getWeeklyOccurrences(session)
        );
  
        console.log("📅 Parsed Calendar Events:", this.calendarOptions.events);
      },
      (error) => {
        this.loading = false;
        this.errorMessage = '⚠️ Failed to load schedule. Please try again later.';
        console.error('❌ Failed to load schedule:', error);
      }
    );
  }
  
  getWeeklyOccurrences(session: any): any[] {
    const occurrences = [];
    const startDate = new Date(session.start_date);
    const repeatUntil = new Date(session.repeat_until);
  
    let currentDate = new Date(startDate);
  
    let correctedDay = session.day_of_week + 1;
    if (correctedDay === 7) correctedDay = 0; // Convert Sunday correctly
  
    const sessionColors: { [key: string]: string } = {
      "Lecture": "#007bff",   // 🔵 Blue
      "Tutorial": "#dc3545",  // 🔴 Red
      "Lab": "#28a745"        // 🟢 Green
    };
  
    while (currentDate <= repeatUntil) {
      let sessionDate = new Date(currentDate);
      const dayOffset = (correctedDay - sessionDate.getDay() + 7) % 7;
      sessionDate.setDate(sessionDate.getDate() + dayOffset);
  
      if (sessionDate > repeatUntil) break;
  
      const startTime = new Date(sessionDate);
      const endTime = new Date(sessionDate);
  
      startTime.setHours(parseInt(session.start_time.split(':')[0], 10));
      startTime.setMinutes(parseInt(session.start_time.split(':')[1], 10));
  
      endTime.setHours(parseInt(session.end_time.split(':')[0], 10));
      endTime.setMinutes(parseInt(session.end_time.split(':')[1], 10));
  
      occurrences.push({
        title: `${session.module} - ${session.session_type}`,
        start: startTime.toISOString(),
        end: endTime.toISOString(),
        allDay: false,
        color: sessionColors[session.session_type] || "#6c757d",
  
        extendedProps: {
          sessionType: session.session_type,
          room: session.room || "TBA",
          lecturer: session.lecturer || "TBA"
        }
      });
  
      currentDate.setDate(currentDate.getDate() + 7);
    }
  
    return occurrences;
  }
  
}  