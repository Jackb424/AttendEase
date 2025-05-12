import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { NavComponent } from './/nav.component';  // ✅ Ensure you import the navigation component

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterModule, NavComponent], // ✅ Make sure NavComponent is imported
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'AttendanceApp';
}
