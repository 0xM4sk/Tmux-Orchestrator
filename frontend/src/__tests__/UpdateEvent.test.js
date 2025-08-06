|
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import UpdateEvent from '../UpdateEvent';

jest.mock('axios');

test('updates an event', async () => {
axios.put.mockResolvedValue({ data: { id: 1, title: 'Updated Event', description: 'This is an updated event' } });

const { getByPlaceholderText, getByText } = render(<UpdateEvent eventId={1} />);

fireEvent.change(getByPlaceholderText('Title'), { target: { value: 'Updated Event' } });
fireEvent.change(getByPlaceholderText('Description'), { target: { value: 'This is an updated event' } });
fireEvent.click(getByText('Update Event'));

await waitFor(() => {
expect(axios.put).toHaveBeenCalledWith('/api/events/1', { title: 'Updated Event', description: 'This is an updated event' });
expect(getByText('Event updated successfully!')).toBeInTheDocument();
});
});