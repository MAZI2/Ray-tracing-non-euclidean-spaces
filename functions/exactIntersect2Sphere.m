function [intersect, o] = exactIntersect2Sphere(T, d)
% Ray trace for 2-Sphere
% step
h = 0.1;
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
maxit = 200;%300;

% intersection point
intersect = [];

% 2sphere radius
R = 2;

% index of intersected object
o = 0;

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
   
    % initialization of y1 y2 y3 y4
    if(step == 0)
        % find sphere center
        Ce = sphereCenter(Tn, d, R);
        
        % move 2sphere to (0, 0)
        Te = Tn-Ce;

        % u
        y1p=acos(Te(3)./R);
        % if y1p is 0, move a bit forward to avoid cot(0)
        if(y1p==0)
            y1p=0.01;
        end
        % du
        y2p=1;
        % v
        y3p=atan2(Te(2), Te(1));
        % dv
        y4p=0;

        % get next point
        [y1t, y2t, y3t, y4t, h] = euler(y1p, y2p, y3p, y4p, h);
        D = uvToVec(y1t, y3t, R)+Ce-Tn;
        % with dot product determine if the direction is correct
        % otherwise change du direction
        if(d*D'<0)
            y2p=-1;
        end
        
    end
    % get next point (perform step)
    [y1t, y2t, y3t, y4t, h] = euler(y1p, y2p, y3p, y4p, h);
    % next point actual coordinates
    Tnt = uvToVec(y1t, y3t, R)+Ce;

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
        y1p=y1t;
        y2p=y2t;
        y3p=y3t;
        y4p=y4t;
        Tn = Tnt;

        %plot3(Tn(1), Tn(2), Tn(3), 'ro');
        %hold on;
    end
    step = step+1;
end