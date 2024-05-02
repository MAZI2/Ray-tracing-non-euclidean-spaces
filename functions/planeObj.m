function [p] = planeObj(a, b, c, d, visualize)
% returns function f(x,y,z) from equation f(x,y,z)=0
% if visualize == true, planeObj will also plot the surface

% plotting
if(visualize)
    rangeX = [-15;15];
    rangeY = [-15;15];
    step = 2;

    % define the range of x and y values
    [x, y] = meshgrid(rangeX(1):step:rangeX(2), rangeY(1):step:rangeY(2));
    
    % calculate corresponding z values using the plane equation
    z = (d - a*x - b*y) / c;
    
    surf(x, y, z);
    hold on
end

% plane function
p = @(x, y, z) a*x + b*y + c*z - d;