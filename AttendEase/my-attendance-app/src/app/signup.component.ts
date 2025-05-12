import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'signup',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './signup.component.html',
  styleUrls: ['./signup.component.css'],
  providers: [AuthService]
})
export class SignupComponent {
  signupForm: FormGroup;

  constructor(private formBuilder: FormBuilder, private authService: AuthService, private router: Router) {
    this.signupForm = this.formBuilder.group({
      b0_number: ['', Validators.required],
      name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
  }

  isInvalid(control: string): boolean {
    const formControl = this.signupForm.get(control);
    return !!formControl?.invalid && !!formControl?.touched;
  }

  onSubmit(): void {
    if (this.signupForm.valid) {
      const formData = this.signupForm.value;
      this.authService.signup(formData).subscribe(
        () => {
          alert('Signup successful! Please log in.');
          this.router.navigate(['/login']);
        },
        error => {
          console.error('Signup failed:', error);
          alert('Signup failed: ' + (error.error.message || 'An unknown error occurred.'));
        }
      );
    }
  }
}
