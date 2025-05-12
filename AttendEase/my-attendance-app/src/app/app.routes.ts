import { Routes } from '@angular/router';
import { HomeComponent } from './home.component';
import { AttendanceComponent } from './attendance.component';
import { LoginComponent } from './login.component';
import { SignupComponent } from './signup.component';
import { ProfileComponent } from './profile.component';
import { EditProfileComponent } from './edit-profile.component';
import { CalendarComponent } from './calendar.component';
import { CameraComponent } from './camera.component'; // ✅ Import Camera Component
import { AdminComponent } from './admin.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'attendance', component: AttendanceComponent },
  { path: 'login', component: LoginComponent },
  { path: 'signup', component: SignupComponent },
  { path: 'profile', component: ProfileComponent },
  { path: 'calendar', component: CalendarComponent },
  { path: 'edit-profile', component: EditProfileComponent },
  { path: 'camera', component: CameraComponent }, // ✅ Add Route for Camera Page
  { path: 'admin', component: AdminComponent },
]; 
