% Define the timeslots with day IDs and durations
timeslot(1..23).

% Define the capacity constraint
capacity(1550).

% Assign each exam to a timeslot
{ assign(E, T) : timeslot(T) } = 1 :- exam(E, _).

% Ensure the total number of students in each timeslot does not exceed the capacity
:- timeslot(T), capacity(C), #sum { 1,S : enrolled(S, E), assign(E, T) } > C.

% Ensure no two students are in the same timeslot for different exams
:- enrolled(S, E1), enrolled(S, E2), E1 != E2, assign(E1, T), assign(E2, T).

% Ensure the timeslot duration is sufficient for the exam
:- assign(E, T), exam(E, D), timeslot(T, _, TD), D > TD.

% Minimize adjacent exams on the same day for each student
adjacency_penalty(S, E1, E2) :- enrolled(S, E1), enrolled(S, E2), E1 != E2, assign(E1, T1), assign(E2, T2), timeslot(T1, D, _), timeslot(T2, D, _), T2 = T1 + 1.
#minimize { 1, S, E1, E2 : adjacency_penalty(S, E1, E2) }.

% Output the assignment of exams to timeslots
#show assign/2.