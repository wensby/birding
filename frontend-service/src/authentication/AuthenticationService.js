export default class AuthenticationService {

  constructor() {
    this.apiUrl = window._env_.API_URL;
  }

  async fetchAuthenticationToken(username, password) {
    const url = `${this.apiUrl}/authentication/token`;
    const parameters = `?username=${username}&password=${password}`;
    return await fetch(url + parameters);
  }

  async postPasswordResetEmail(email) {
    const response = await fetch(
      `${this.apiUrl}/authentication/password-reset`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          'email': email,
        }),
      }
    );
    return await response.json();
  }

  async postPasswordResetPassword(token, password) {
    const response = await fetch(
      `${this.apiUrl}/authentication/password-reset/${token}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          'password': password
        })
      }
    );
    return await response.json();
  }

  async postPasswordUpdate(accessToken, oldPassword, newPassword) {
    return await fetch(`${this.apiUrl}/authentication/password`, {
      method: 'POST',
      headers: {
        'accessToken': accessToken,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        'oldPassword': oldPassword,
        'newPassword': newPassword,
      }),
    });
  }

  async postRegistrationEmail(email) {
    const url = `${this.apiUrl}/authentication/registration`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        'email': email,
      })
    })
    return await response.json();
  }

  async fetchRegistration(token) {
    try {
      const url = `${this.apiUrl}/authentication/registration/${token}`;
      const response = await fetch(url);
      const json = await response.json();
      return json['result']['registration'];
    }
    catch (err) {
      return undefined;
    }
  }

  async postRegistration(token, [username, password]) {
    try {
      const url = `${this.apiUrl}/authentication/registration/${token}`;
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          'username': username,
          'password': password,
        })
      })
      return await response.json();
    }
    catch (err) {
      return undefined;
    }
  }

  async logout() {
    localStorage.removeItem('accessToken');
  }
}
