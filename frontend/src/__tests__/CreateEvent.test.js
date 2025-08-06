|
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import CreateEvent from '../CreateEvent';

jest.mock('axios');

test('creates an event', async () => {
axios.post.mockResolvedValue({ data: { id: 1, title: 'Test Event', description: 'This is a test event' } });

const { getByPlaceholderText, getByText } = render(<CreateEvent />);

fireEvent.change(getByPlaceholderText('Title'), { target: { value: 'Test Event' } });
fireEvent.change(getByPlaceholderText('Description'), { target: { value: 'This is a test event' } });
fireEvent.click(getByText('Create Event'));

await waitFor(() => {
expect(axios.post).toHaveBeenCalledWith('/api/events', { title: 'Test Event', description: 'This is a test event' });
expect(getByText('Event created successfully!')).toBeInTheDocument();
});
});