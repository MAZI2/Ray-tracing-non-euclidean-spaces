function [C] = sphereCenter(T, d, R)
% cross product straight down x direction d(ray) -> circle plane normal n
n=cross([0,0,-1], d);
% cross product direction x normal -> a vector in circle plane perpendicular to ray
C=cross(d, n);
% normalize and extend to length R ... C = center of 2-sphere 
C=(C./norm(C)).*R+T;