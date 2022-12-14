import torch
from .Module import Module
from .utils import addSingletonDimension

class Unsqueeze(Module):

    def __init__(self, dim):
        super(Unsqueeze, self).__init__()
        self.dim = dim

    def updateOutput(self, input):
        addSingletonDimension(self.output, input, self.dim)
        return self.output

    def updateGradInput(self, input, gradOutput):
        assert input.nElement() == gradOutput.nElement()
        self.gradInput = gradOutput.view(input.size())
        return self.gradInput

    def __repr__(self):
        return super(Unsqueeze, self).__repr__() + '({})'.format(self.dim)

