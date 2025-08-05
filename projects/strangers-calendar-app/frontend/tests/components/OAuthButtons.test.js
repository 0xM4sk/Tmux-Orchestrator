|
import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import OAuthButtons from '../components/OAuthButtons';

jest.mock('axios', () => ({
get: jest.fn()
}));

test('GoogleOAuthButton should handle successful response correctly', async () => {
const axiosGetMock = axios.get;
axiosGetMock.mockResolvedValueOnce({ data: { access_token: 'fake-token' } });

const { getByText } = render(<OAuthButtons />);
fireEvent.click(getByText('Login with Google'));

expect(axiosGetMock).toHaveBeenCalledWith('https://oauth.google.com/token', {
params: {
code: expect.any(String),
client_id: expect.any(String),
redirect_uri: expect.any(String),
grant_type: 'authorization_code'
}
});
});

test('GoogleOAuthButton should handle error response correctly', async () => {
const axiosGetMock = axios.get;
axiosGetMock.mockRejectedValueOnce(new Error('Invalid token'));

const { getByText } = render(<OAuthButtons />);
fireEvent.click(getByText('Login with Google'));

await expect(axiosGetMock).toHaveBeenCalledWith('https://oauth.google.com/token', {
params: {
code: expect.any(String),
client_id: expect.any(String),
redirect_uri: expect.any(String),
grant_type: 'authorization_code'
}
});
});