function [X, I] = camera()
% returns array X of 3d ray vectors
% returns image_height x image_width x 3 image I
% bottom_left, bottom_right, upper_left, upper_right define the image plane
% resolution is the amount of steps the image will be divided into
% point is the position of the camera

X = [];
I = [];

bottom_left = [0, 2, 0]';
bottom_right = [2, 0, 0]';
upper_left = [0, 2, 2]';
upper_right = [2, 0, 2]';

resolution = 10;
point = [0, 0, 1]';

image_width = 10;
image_height = 10;

right_step = (bottom_right-bottom_left)./resolution;
up_step = (upper_left-bottom_left)./resolution;

% calculate vectors from camera to the points on image
for i=0:image_width
    for j=0:image_height
        v = bottom_left + i*right_step + j*up_step - point;
        X = [X v];

        % plotting the vectors 
        % quiver3(point(1), point(2), point(3), v(1), v(2), v(3));
        % hold on
    end
end
% axis equal

I = zeros(image_height, image_width, 3); 
