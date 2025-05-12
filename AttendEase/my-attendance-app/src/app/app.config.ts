import { ApplicationConfig } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter } from '@angular/router';

import { AuthService } from '../services/auth.service';
import { AttendanceService } from '../services/attendance.service';

import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(), // ✅ Ensures HttpClient is globally available
    provideRouter(routes),
    AuthService,
    AttendanceService
  ]
};
