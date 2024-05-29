function [y] = findLight(L, Int)
% Trace ray towards a light source

% objects ------- hardcoded 2 spheres, 1 plane
% spheres (array)
C1 = [2, 2, -1];
C2 = [0, 0, -2];
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

% step
h = 0.1;
% unit direction
d = L - Int;
d = d./norm(d);

% initial signs for objects (moved 1 step forward)
signs(1) = sign(f(Int+h*d, O(:, 1)', r(1)));
signs(2) = sign(f(Int+h*d, O(:, 2)', r(2)));
signs(3) = sign(fPlane(Int+h*d, A));

% max iterations
maxit = 500;

step = 1;
while true
    if(step == maxit)
        y=-1;
        break;
    end
    % vector
    v = h*step*d;
    % current point
    T = v+Int;
    % check if sign has changed
    for i=1:objs
        % hardcoded for 2 spheres, 1 plane
        % plane
        if(i==3)
            if(sign(fPlane(T, A)) == -signs(i))
                y = 1;
                return
            end
        % spheres
        elseif(sign(f(T, O(:, i)', r(i))) == -signs(i))
            y = 1;
            return
        end
    end
    %plot3(v(1)+Int(1), v(2)+Int(2), v(3)+Int(3), 'bo');
    %hold on
    
    % dot product between the light and intersect * light and current point
    % if < 0, already passed
    y = sign((L-Int)*(L - T)');
    if(y == -1)
        break
    end
    step = step + 1;
end