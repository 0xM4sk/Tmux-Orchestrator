|
import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import SearchEvent from './SearchEvent';

test('searches events by keyword', async () => {
const mockEvents = [
{ id: 1, title: 'Tech Conference' },
{ id: 2, title: 'Workshop on React' },
{ id: 3, title: 'Lunch and Learn' }
];

render(<SearchEvent events={mockEvents} />);
fireEvent.change(screen.getByPlaceholderText('Search events...'), {
target: { value: 'React' }
});

expect(screen.getAllByText(/react/i)).toHaveLength(1);
});