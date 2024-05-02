function [objects] = scene(visualize)
% return array of functions f(x,y,z) from equations f(x,y,z)=0 for surfaces defined inside objects[]
% if visualize == true, plot the surfaces defined inside objects[]

objects = {
    sphereObj(5, 5, 5, 2, visualize),
    sphereObj(5, 7, 10, 1, visualize),
    planeObj(5, 10, 5, 200, visualize)
}

if(visualize)
    axis equal
end