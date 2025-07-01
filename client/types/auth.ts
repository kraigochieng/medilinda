export interface LoginCredentials {
	username: string;
	password: string;
}

export interface SignUpDetails {
	username: string;
	password: string;
	firstName: string;
	lastName: string;
}

export interface TokenRefreshResponse {
	accessToken: string;
	tokenType: string;
}

export interface TokenResponse {
	access_token: string;
	refresh_token: string;
	token_type: string;
}
