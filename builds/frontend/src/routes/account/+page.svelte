<script>
    let user = {
      name: 'John Doe',
      email: 'john.doe@example.com',
      phone: '123-456-7890'
    };
  
    let newPassword = '';
    let confirmPassword = '';
  
    let notificationPreferences = {
      email: true,
      push: false,
      sms: true
    };
  
    function updateProfile() {
      // Implement profile update logic here
      console.log('Profile updated:', user);
    }
  
    function changePassword() {
      // Implement password change logic here
      if (newPassword === confirmPassword) {
        console.log('Password changed');
        newPassword = '';
        confirmPassword = '';
      } else {
        alert('Passwords do not match');
      }
    }
  
    function updateNotifications() {
      // Implement notification preferences update logic here
      console.log('Notification preferences updated:', notificationPreferences);
    }
  </script>
  
  <main class="container mx-auto p-4">
    <h1 class="text-3xl font-bold mb-6">Account Settings</h1>
  
    <div class="space-y-8">
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">Personal Information</h2>
          <form on:submit|preventDefault={updateProfile} class="space-y-4">
            <div class="form-control">
              <label for="name" class="label">Name</label>
              <input type="text" id="name" bind:value={user.name} class="input input-bordered" />
            </div>
            <div class="form-control">
              <label for="email" class="label">Email</label>
              <input type="email" id="email" bind:value={user.email} class="input input-bordered" />
            </div>
            <div class="form-control">
              <label for="phone" class="label">Phone</label>
              <input type="tel" id="phone" bind:value={user.phone} class="input input-bordered" />
            </div>
            <button type="submit" class="btn btn-primary">Update Profile</button>
          </form>
        </div>
      </div>
  
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">Change Password</h2>
          <form on:submit|preventDefault={changePassword} class="space-y-4">
            <div class="form-control">
              <label for="newPassword" class="label">New Password</label>
              <input type="password" id="newPassword" bind:value={newPassword} class="input input-bordered" />
            </div>
            <div class="form-control">
              <label for="confirmPassword" class="label">Confirm Password</label>
              <input type="password" id="confirmPassword" bind:value={confirmPassword} class="input input-bordered" />
            </div>
            <button type="submit" class="btn btn-primary">Change Password</button>
          </form>
        </div>
      </div>
  
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">Notification Preferences</h2>
          <form on:submit|preventDefault={updateNotifications} class="space-y-4">
            <div class="form-control">
              <label class="label cursor-pointer">
                <span class="label-text">Email Notifications</span>
                <input type="checkbox" bind:checked={notificationPreferences.email} class="toggle" />
              </label>
            </div>
            <div class="form-control">
              <label class="label cursor-pointer">
                <span class="label-text">Push Notifications</span>
                <input type="checkbox" bind:checked={notificationPreferences.push} class="toggle" />
              </label>
            </div>
            <div class="form-control">
              <label class="label cursor-pointer">
                <span class="label-text">SMS Notifications</span>
                <input type="checkbox" bind:checked={notificationPreferences.sms} class="toggle" />
              </label>
            </div>
            <button type="submit" class="btn btn-primary">Update Preferences</button>
          </form>
        </div>
      </div>
    </div>
  </main>
