let currentStep = 1;
let verificationInProgress = false;
const MAX_ATTEMPTS = 3;
let attemptCount = 0;

// Format number with commas
function formatNumber(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function validateStep(step) {
  if (step === 1) {
    const value = parseInt(document.getElementById('creditsInput').value);
    if (!value || value < 10000) {
      alert('Minimum purchase amount is 10,000 credits');
      return false;
    }
  }
  return true;
}

function updateBank(bank) {
  document.getElementById('bankInput').value = bank;
  document.getElementById('confirmBank').textContent = bank;
}

function showStep(step) {
  ['select-credits', 'payment-method', 'confirm'].forEach(id => {
    const element = document.getElementById(id);
    if (element) {
      element.classList.add('d-none');
      element.classList.remove('active');
    }
  });

  const currentElement = document.getElementById(
    step === 1 ? 'select-credits' :
    step === 2 ? 'payment-method' :
    'confirm'
  );

  if (currentElement) {
    currentElement.classList.remove('d-none');
    currentElement.classList.add('active');
  }

  updateStepProgress(step);
}

function updateStepProgress(step) {
  document.querySelectorAll('.step-circle').forEach((circle, index) => {
    if (index + 1 < step) {
      circle.classList.add('completed');
      circle.classList.remove('active');
    } else if (index + 1 === step) {
      circle.classList.add('active');
      circle.classList.remove('completed');
    } else {
      circle.classList.remove('active', 'completed');
    }
  });
}

function prevStep(step) {
  currentStep = step;
  showStep(step);
}

function nextStep(step) {
  if (validateStep(currentStep)) {
    currentStep = step;
    if (step === 3) {
      sendVerificationCode();
    } else {
      showStep(step);
    }
  }
}

async function sendVerificationCode() {
  if (verificationInProgress) return;
  verificationInProgress = true;

  try {
    const response = await fetch(URLS.sendCode, {
      method: 'POST',
      headers: {
        'X-CSRFToken': CSRF_TOKEN,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        credits: document.getElementById('creditsInput').value,
      })
    });

    if (response.ok) {
      showStep(3);
      document.getElementById('verificationAlert').classList.remove('d-none');
      document.getElementById('errorAlert').classList.add('d-none');
      document.getElementById('verificationMessage').textContent = '';
    } else {
      throw new Error('Failed to send verification code');
    }
  } catch (error) {
    console.error('Error:', error);
  } finally {
    verificationInProgress = false;
  }
}

async function verifyCodeAndProceed() {
  const code = document.getElementById('verificationCode').value;
  if (!code || code.length !== 5) {
    document.getElementById('verificationMessage').textContent = 'Please enter a valid 5-digit code';
    return;
  }

  try {
    const response = await fetch(URLS.verifyCode, {
      method: 'POST',
      headers: {
        'X-CSRFToken': CSRF_TOKEN,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        code: code,
        credits: document.getElementById('creditsInput').value,
      })
    });

    const data = await response.json();

    if (data.success) {
      document.getElementById('errorAlert').classList.add('d-none');
      document.getElementById('verificationMessage').textContent = 'Code verified successfully!';
      document.getElementById('verificationMessage').classList.remove('text-danger');
      document.getElementById('verificationMessage').classList.add('text-success');

      setTimeout(() => {
        document.getElementById('purchaseForm').submit();
      }, 1000);
    } else {
      attemptCount++;
      const remainingAttempts = MAX_ATTEMPTS - attemptCount;

      const errorAlert = document.getElementById('errorAlert');
      errorAlert.classList.remove('d-none');

      if (remainingAttempts > 0) {
        errorAlert.innerHTML = `<p>Invalid code. ${remainingAttempts} ${remainingAttempts === 1 ? 'attempt' : 'attempts'} remaining.</p>`;
      } else {
        errorAlert.innerHTML = '<p>Maximum attempts reached. Please start over.</p>';
        document.getElementById('verifyAndProceed').disabled = true;
        document.getElementById('verificationCode').disabled = true;

        setTimeout(() => {
          window.location.reload();
        }, 3000);
      }
    }
  } catch (error) {
    console.error('Error:', error);
    document.getElementById('verificationMessage').textContent = 'Error verifying code';
  }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
  const creditsInput = document.getElementById('creditsInput');

  // Initialize values on page load
  updateDisplayValues(10000);

  creditsInput.addEventListener('input', function() {
    // Permitir que el campo esté vacío temporalmente
    if (this.value === '') {
      updateDisplayValues(0);
      return;
    }

    let value = parseInt(this.value);
    if (isNaN(value)) {
      value = 10000;
      this.value = value;
    }
    updateDisplayValues(value);
  });

  // Validar el mínimo cuando el campo pierde el foco
  creditsInput.addEventListener('blur', function() {
    let value = parseInt(this.value) || 0;
    if (value < 10000) {
      value = 10000;
      this.value = value;
      updateDisplayValues(value);
    }
  });

  document.getElementById('resendCode').addEventListener('click', sendVerificationCode);
});

function updateDisplayValues(value) {
  const formattedValue = formatNumber(value);
  const elements = {
    'totalValue': formattedValue,
    'summaryCredits': formattedValue,
    'summaryTotal': `$${formattedValue}`,
    'confirmCredits': formattedValue,
    'confirmTotal': `$${formattedValue}`
  };

  Object.entries(elements).forEach(([id, value]) => {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
  });
}
