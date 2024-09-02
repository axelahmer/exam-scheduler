#const tmax = 23.
#const capacity = 1550.

% Imported predicates:
% exam(ExamID, Duration)
%   ExamID: unique identifier for the exam (atom)
%   Duration: length of the exam in minutes (integer)

% enrolled(StudentID, ExamID)
%   StudentID: unique identifier for the student (atom)
%   ExamID: unique identifier for the exam (atom)

% timeslot(TimeslotID, DayID, Duration)
%   TimeslotID: unique identifier for the timeslot (integer, 1..tmax)
%   DayID: identifier for the day (integer)
%   Duration: length of the timeslot in minutes (integer)

% Define the timeslots with day IDs and durations
timeslot(1..tmax).

% Assign each exam to a timeslot, but only if it could be assigned
{ assign(E, T) : timeslot(T), timeslot(T, _, TD), D <= TD } = 1 :- exam(E, D).

% Calculate the number of students for each exam
exam_student_count(E, C) :- exam(E, _), C = #count { S : enrolled(S, E) }.

% Ensure the total number of students in each timeslot does not exceed the capacity
:- timeslot(T), #sum { SC,E : exam_student_count(E, SC), assign(E, T) } > capacity.

% Ensure no two students are in the same timeslot for different exams
:- enrolled(S, E1), enrolled(S, E2), E1 != E2, assign(E1, T), assign(E2, T).

% Minimize adjacent exams on the same day for each student
adjacency_penalty(S, E1, E2) :- enrolled(S, E1), enrolled(S, E2), E1 != E2, assign(E1, T1), assign(E2, T2), timeslot(T1, D, _), timeslot(T2, D, _), T2 = T1 + 1.
#minimize { 1, S, E1, E2 : adjacency_penalty(S, E1, E2) }.

% Output the assignment of exams to timeslots and student counts
#show assign/2.
% #show timeslot_student_count/2.