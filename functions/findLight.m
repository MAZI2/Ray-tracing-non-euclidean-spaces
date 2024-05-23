function [y] = findLight(L, Int)
% Trace a ray toward a light source

% objects
C1 = [2, 2, -1];
C2 = [0, 0, -2];
r1 = 1;
r2 = 0.5;
O = [C1' C2'];
r = [r1, r2];
objs = 2;
signs = [0, 0];
% --------

h = 0.1;
d = L - Int;
d = d./norm(d);

% signs for 2 spheres
signs(1) = sign(f(Int+h*d, O(:, 1)', r(1)));
signs(2) = sign(f(Int+h*d, O(:, 2)', r(2)));

maxit = 500;

step = 1;
while true
    if(step == maxit)
        y=-1;
        break;
    end
    v = h*step*d;
    T = v+Int;
    for i=1:objs
        if(sign(f(T, O(:, i)', r(i))) == -signs(i))
            y = 1;
            return
        end
    end
    %plot3(v(1)+Int(1), v(2)+Int(2), v(3)+Int(3), 'bo');
    %hold on
    y = sign((L-Int)*(L - T)');
    if(y == -1)
        break
    end
    step = step + 1;
end