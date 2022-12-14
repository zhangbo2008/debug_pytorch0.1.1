import torch
from .Criterion import Criterion

class WeightedMSECriterion(Criterion):

    def __init__(self, weight, sizeAverage=True):
        super(WeightedMSECriterion, self).__init__()
        self.weight = weight.clone()
        self.buffer = None
        self.output_tensor = None
        self.sizeAverage = sizeAverage

    def updateOutput(self, input, target):
        self.buffer = self.buffer or input.new()
        self.buffer.resizeAs_(input).copy_(target)
        if input.dim() - 1 == self.weight.dim():
            for i in range(input.size(0)):
                self.buffer[i].mul_(self.weight)
        else:
            self.buffer.mul_(self.weight)

        self.output_tensor = self.output_tensor or input.new(1)
        self._backend.MSECriterion_updateOutput(
            self._backend.library_state,
            input,
            self.buffer,
            self.output_tensor,
            self.sizeAverage
        )
        self.output = self.output_tensor[0]
        return self.output

    def updateGradInput(self, input, target):
        self.buffer.resizeAs_(input).copy_(target)
        if input.dim() - 1 == self.weight.dim():
            for i in range(input.size(0)):
                self.buffer[i].mul_(self.weight)
        else:
            self.buffer.mul_(self.weight)

        self._backend.MSECriterion_updateGradInput(
            self._backend.library_state,
            input,
            self.buffer,
            self.gradInput,
            self.sizeAverage
        )
        return self.gradInput

