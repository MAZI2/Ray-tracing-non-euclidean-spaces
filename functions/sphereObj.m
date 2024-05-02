function [p] = sphereObj(x0, y0, z0, R, visualize)
% returns function f(x,y,z) from equation f(x,y,z)=0
% if visualize == true, sphereObj will also plot the surface

% plotting
if(visualize)
    numPoints = 10;
    [X, Y, Z] = sphere(numPoints);

    X = R*X + x0;
    Y = R*Y + y0;
    Z = R*Z + z0;
    
    surf(X, Y, Z)
    hold on
end

% plane function
p = @(x, y, z) (x-x0).^2 + (y-y0).^2 + (z-z0).^2 - R.^2;