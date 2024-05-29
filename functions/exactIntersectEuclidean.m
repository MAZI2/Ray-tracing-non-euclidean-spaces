function [intersect, o] = exactIntersectEuclidean(T, d)
% Ray trace for Euclidean space
% step
h = 0.13;
% tolerance for exact intersect
eps = 0.01;

% objects ------- hardcoded 2 spheres, 1 plane
% spheres (array)
C1 = [2, 2, -1];
C2 = [4, 5, 0];
r1 = 1;
r2 = 0.5;
O = [C1' C2'];
r = [r1, r2];
% plane (1 object)
% a b c d
A = [-0.2, -0.2, 1, -3];
% ---------------
objs = 3;
signs = [0, 0, 0];

% initial signs for objects (moved 1 step forward)
signs(1) = sign(f(T, O(:, 1)', r(1)));
signs(2) = sign(f(T, O(:, 2)', r(2)));
signs(3) = sign(fPlane(T, A));

% current point
Tn = T;
% next point
Tnt = Tn;

% max iterations
maxit = 300;%300;

% intersection point
intersect = [];

% index of intersected object
o = 0;

% normalize direction
d = d./norm(d);

step = 0;
while true
    if(step == maxit)
        break
    end
    % check if distance to objects is < eps
    for i=1:objs
        % hardcoded for 2 spheres, 1 plane
        % plane
        if(i==3)
            if(distPlane(Tn, A) < eps)
                intersect = Tn;
                o = i;
                break
            end
        % spheres
        elseif(dist(Tn, O(:, i)', r(i)) < eps)
            intersect = Tn;
            o = i;
            break
        end
    end
   
    % get next point (perform step)
    Tnt = Tn + h.*d;

    % check signs
    % h = h/2 if changed
    changed = 0;
    for i=1:objs
        % hardcoded for 2 spheres, 1 plane
        % plane
        if(i==3)
            if(sign(fPlane(Tnt, A)) == -signs(i))
                h=h./2;
                changed = 1;
                break
            end
        % spheres
        elseif(sign(f(Tnt, O(:, i)', r(i))) == -signs(i))
            h=h./2;
            changed = 1;
            break
        end
    end
    
    % if the sign hasn't changed, move one step
    if(changed == 0)
        Tn = Tnt;
        %plot3(Tn(1), Tn(2), Tn(3), 'ro');
        %hold on;
    end
    step = step+1;
end