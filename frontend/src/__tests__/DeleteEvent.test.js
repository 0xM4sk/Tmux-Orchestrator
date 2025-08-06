|
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import DeleteEvent from '../DeleteEvent';

jest.mock('axios');

test('deletes an event', async () => {
axios.delete.mockResolvedValue({ status: 204 });

const { getByText } = render(<DeleteEvent eventId={1} />);

fireEvent.click(getByText('Delete Event'));

await waitFor(() => {
expect(axios.delete).toHaveBeenCalledWith('/api/events/1');
expect(getByText('Event deleted successfully!')).toBeInTheDocument();
});
});