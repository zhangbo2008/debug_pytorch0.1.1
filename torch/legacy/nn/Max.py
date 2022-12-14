import torch
from .Module import Module
from .utils import clear, addSingletonDimension

class Max(Module):

    def __init__(self, dimension=0):
        super(Max, self).__init__()
        self.dimension = dimension
        self._output = None
        self._indices = None

    def _getPositiveDimension(self, input):
        dimension = self.dimension
        if dimension < 0:
           dimension = input.dim() + dimension

        return dimension

    def _lazyInit(self):
        self._output = self._output or self.output.new()
        self._indices = self._indices or \
           (torch.cuda.LongTensor() if torch.typename(self.output) == 'torch.cuda.FloatTensor' else torch.LongTensor())

    def updateOutput(self, input):
        self._lazyInit()
        dimension = self._getPositiveDimension(input)
        torch.max(self._output, self._indices, input, dimension)
        if input.dim() > 1:
          self.output.set_(self._output.select(dimension, 0))
        else:
          self.output.set_(self._output)

        return self.output

    def updateGradInput(self, input, gradOutput):
        self._lazyInit()
        dimension = self._getPositiveDimension(input)
        if input.dim() > 1:
          gradOutputView = addSingletonDimension(gradOutput, dimension)
        else:
          gradOutputView = gradOutput

        self.gradInput.resizeAs_(input).zero_().scatter_(dimension, self._indices, gradOutputView)
        return self.gradInput

    def type(self, type, tensorCache=None):
        # torch.max expects a LongTensor as indices, whereas cutorch.max expects a CudaTensor.
        if type == 'torch.cuda.FloatTensor':
            indices, self._indices = self._indices, None
            super(Max, self).type(type, tensorCache)
            self._indices = indices.type('torch.cuda.LongTensor') if indices else None
        else:
            # self._indices must be a LongTensor. Setting it to nil temporarily avoids
            # unnecessary memory allocations.
            indices, self._indices = self._indices, None
            super(Max, self).type(type, tensorCache)
            self._indices = indices.long() if indices else None

        return self

    def clearState(self):
        clear(self, '_indices', '_output')
        return super(Max, self).clearState()

