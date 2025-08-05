|
import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import OAuthButtons from './OAuthButtons';

jest.mock('../services/oauth_service', () => ({
OAuthClient: {
loginWithGoogle: jest.fn(),
loginWithApple: jest.fn(),
},
}));

describe('OAuth Buttons', () => {
it('should handle Google login correctly', async () => {
const { getByText } = render(
<MemoryRouter>
<OAuthButtons />
</MemoryRouter>
);

fireEvent.click(getByText('Login with Google'));

expect(OAuthClient.loginWithGoogle).toHaveBeenCalled();
});

it('should handle Apple login correctly', async () => {
const { getByText } = render(
<MemoryRouter>
<OAuthButtons />
</MemoryRouter>
);

fireEvent.click(getByText('Login with Apple'));

expect(OAuthClient.loginWithApple).toHaveBeenCalled();
});
});