function [C] = sphereCenter(T, d, R)
% cross product straight down x direction d(ray) -> circle plane normal n
n=cross([0,0,-1], d);
% cross product direction x normal -> a vector in circle plane perpendicular to ray
C=cross(d, n);
% normalize and extend to length R ... C = center of 2-sphere 
C=(C./norm(C)).*R+T;



% plotting
% draw camera
%plot3(T(1), T(2), T(3), 'ro');
%hold on
% draw ray
%p2=T+d;
%plot3(p2(1), p2(2), p2(3), 'ro');
% draw 2-sphere center
%plot3(C(1), C(2), C(3), 'bo');

%axis equal