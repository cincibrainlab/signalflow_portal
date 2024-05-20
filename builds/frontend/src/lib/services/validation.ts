export function validateEmail(emailSelection: string | null, newEmailAddress: string | null) {
    return !emailSelection || (emailSelection === 'enter_new' && !newEmailAddress) ? 'Please select an email address before submitting.' : null;
  }
  
  export function validateEEGFormat(eegFormat: string | null) {
    return !eegFormat ? 'Please select an EEG format before submitting.' : null;
  }
  
  export function validateEEGParadigm(eegParadigm: string | null) {
    return !eegParadigm ? 'Please select an EEG paradigm before submitting.' : null;
  }