import { Component, ViewEncapsulation } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'login',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
  providers: [AuthService],
  encapsulation: ViewEncapsulation.None
})
export class LoginComponent {
  loginForm: FormGroup;
  message: string = '';

  constructor(private formBuilder: FormBuilder, private authService: AuthService, private router: Router) {
    this.loginForm = this.formBuilder.group({
      b0_number: ['', Validators.required],
      password: ['', Validators.required]
    });
  }

  isInvalid(control: string): boolean {
    const formControl = this.loginForm.get(control);
    return !!formControl?.invalid && !!formControl?.touched;
  }

  onSubmit(): void {
    if (this.loginForm.valid) {
      const { b0_number, password } = this.loginForm.value;
      console.log("📩 Attempting login with:", { b0_number, password });

      this.authService.login(b0_number, password).subscribe({
        next: response => {
          console.log("✅ Login successful!", response);
          localStorage.setItem('x-access-token', response['x-access-token']);
          this.message = 'Login successful! Redirecting...';

          // Dispatch login success event
          window.dispatchEvent(new CustomEvent('loginSuccess'));

          // Redirect to Profile
          this.router.navigate(['/profile']);
        },
        error: error => {
          console.error("❌ Login failed:", error);
          this.message = 'Login failed: ' + (error.error?.message || 'Unknown error');
        }
      });
    } else {
      this.message = 'Please fill in all required fields.';
      console.warn("⚠️ Form is invalid");
    }
  }
}
